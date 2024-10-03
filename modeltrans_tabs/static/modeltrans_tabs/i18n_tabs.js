(() => {
    const currentLanguage = document.documentElement.lang;

    const addEventListeners = ({ defaultField, fields }) => {
        const parent = fields[0] ? fields[0].closest(".i18n-tabs") : null;

        fields.forEach((field) => {
            if (field) {
                const fieldLanguage = field.dataset.i18nLang;

                if (field.dataset.i18nDefault) {
                    // Synchronize value with the default field
                    field.addEventListener("input", () => {
                        defaultField.value = field.value;
                    });
                }

                const tabButton = parent.querySelector(
                    `.i18n-button[data-i18n-lang=${fieldLanguage}]`
                );
                tabButton.addEventListener("click", () => {
                    document.querySelectorAll(".i18n-button").forEach((button) => {
                        if (button.dataset.i18nLang === fieldLanguage) {
                            button.classList.add("active");
                        } else {
                            button.classList.remove("active");
                        }
                    });
                    document.querySelectorAll(".i18n-tab").forEach((tab) => {
                        if (tab.dataset.i18nLang === fieldLanguage) {
                            tab.classList.remove("hidden");
                        } else {
                            tab.classList.add("hidden");
                        }
                    });

                    field.focus();
                    field.selectionStart = field.value.length;
                });
            }
        });
    };

    document.addEventListener("DOMContentLoaded", () => {
        const i18nFields = document.querySelectorAll("[data-i18n-field]");
        const fieldGroups = {};

        i18nFields.forEach((field) => {
            let formset, formsetIndex;
            let translatedField = field.dataset.i18nField;

            // Check if we're in a formset
            const formsetsContainer = field.closest("[data-inline-formset]");
            if (
                formsetsContainer &&
                !formsetsContainer.dataset.formsetListener
            ) {
                formsetsContainer.addEventListener("formset:added", (event) => {
                    const formsetContainer = event.target;
                    const formsetIndex = event.target.id.match(/\d+/)[0];
                    let groupNames = [translatedField];
                    if (event.target.querySelectorAll("fieldset .form-row").length) {
                        groupNames = Object.keys(fieldGroups).filter(k => k.includes("__prefix__"))
                    }
                    groupNames.forEach(groupName => {
                        const templateGroup = fieldGroups[groupName];
                        let prefix = "__prefix__"
                        let replaceIndex = formsetIndex
                        const match = groupName.match(/^([a-zA-Z][^\s-]*)-([0-9]+)-([^\s-]+$)/)
                        if (match) {
                            prefix = `-${match[2]}-`
                            replaceIndex = `-${formsetIndex}-`
                        }
                        const newGroupName = groupName.replace(prefix, replaceIndex);

                        fieldGroups[newGroupName] = {
                            defaultField: formsetContainer.querySelector(
                                `[name=${newGroupName}]`
                            ),
                            fields: templateGroup.fields.map((field) => {
                                if (!field) return null
                                let prefix = "__prefix__"
                                let replaceIndex = formsetIndex
                                const match = field.name.match(/^([a-zA-Z][^\s-]*)-([0-9]+)-([^\s-]+$)/)
                                if (match) {
                                    prefix = `-${match[2]}-`
                                    replaceIndex = `-${formsetIndex}-`
                                }
                                return formsetContainer.querySelector(
                                    `[name=${field.name.replace(prefix, replaceIndex)}]`
                                );
                            }),
                            isTemplate: false,
                        };

                        // Re-run the script to add tabs to the new formset
                        const { defaultField, fields } = fieldGroups[newGroupName];
                        addEventListeners({ defaultField, fields });
                    })
                });
                formsetsContainer.dataset.formsetListener = true;
            }

            if (formsetsContainer) {
                formset = JSON.parse(formsetsContainer.dataset.inlineFormset);
                // Get current index
                const formsetContainer = field.closest(
                    `[id^=${formset.options.prefix}]`
                );

                if (formsetContainer.id == `${formset.options.prefix}-empty`) {
                    formsetIndex = "__prefix__";
                } else {
                    formsetIndex = formsetContainer.id.match(/\d+/)[0];
                }
                translatedField = `${formset.options.prefix}-${formsetIndex}-${field.dataset.i18nField}`;
            }

            if (!fieldGroups[translatedField]) {
                let selector = `[name=${translatedField}]`;
                let defaultField = field
                    .closest(".form-multiline")
                    ?.querySelector(selector);
                if (!defaultField) {
                    defaultField = field
                    .parentElement
                    ?.parentElement
                    ?.querySelector(selector);
                }

                fieldGroups[translatedField] = {
                    defaultField: defaultField,
                    fields: [],
                    isTemplate: formsetIndex === "__prefix__",
                };
            }
            fieldGroups[translatedField].fields.push(field);
        });

        for (const group in fieldGroups) {
            const { defaultField, fields, isTemplate } = fieldGroups[group];
            let parent = fields[0].closest(".form-multiline");
            if (!parent) {
                parent = fields[0].parentElement
            }

            let errorlist = null;
            let helptext = null;
            if (defaultField) {
                const groupLabel = document.createElement("label");
                groupLabel.textContent = defaultField.labels.length ? defaultField.labels[0].textContent : "";
                errorlist = parent.querySelector(".errorlist");

                if (defaultField.required) {
                    groupLabel.classList.add("required");
                }
                if (defaultField.hasAttribute("aria-describedby")) {
                    helptext = document.getElementById(
                        defaultField.getAttribute("aria-describedby")
                    );
                }
                parent.replaceChildren(groupLabel);
            } else {
                console.error(`Error setting up tabs for ${group}, aborting.`);
                continue;
            }

            const tabs = document.createElement("div");
            tabs.classList.add("i18n-tabs");

            const tabButtons = document.createElement("div");
            tabButtons.classList.add("i18n-tab-buttons");
            tabs.appendChild(tabButtons);

            tabs.appendChild(defaultField);
            defaultField.classList.add("hidden");

            fields.forEach((field) => {
                const fieldLanguage = field.dataset.i18nLang;

                const tabButton = document.createElement("button");
                tabButton.type = "button";
                tabButton.classList.add("i18n-button");
                tabButton.dataset.i18nLang = fieldLanguage;
                tabButton.textContent = fieldLanguage;

                const tab = document.createElement("div");
                tab.classList.add("i18n-tab");
                tab.dataset.i18nLang = fieldLanguage;
                if (defaultField.placeholder) {
                    field.placeholder = defaultField.placeholder;
                }
                tab.appendChild(field);

                if (field.dataset.i18nDefault && defaultField.ariaInvalid) {
                    tabButton.classList.add("errors");
                    tab.classList.add("errors");
                }
                tabButtons.appendChild(tabButton);

                // Enable the currently active language
                if (fieldLanguage === currentLanguage) {
                    tabButton.classList.add("active");
                } else {
                    tab.classList.add("hidden");
                }
                tabs.appendChild(tab);
                const columnName = `column-${field.dataset.i18nField}_${fieldLanguage.replace("-","_")}`
                const fieldName = `field-${field.dataset.i18nField}_${fieldLanguage.replace("-","_")}`
                const fieldParent = document.getElementById(`${field.id.split("-")[0]}-group`.substring(3))
                if (fieldParent) {
                    if (fieldParent.querySelectorAll(`.${columnName}`).length) {
                        fieldParent.querySelectorAll(`.${columnName}`).forEach(n => n.classList.add("hidden"))
                        fieldParent.querySelectorAll(`.field-${field.dataset.i18nField}`).forEach(n => n.classList.add("hidden"))
                        fieldParent.querySelectorAll(`.${fieldName}`).forEach(n => {
                            if (fieldLanguage !== currentLanguage) {
                                n.classList.add("hidden")
                            }
                        })
                    }
                }
            });

            if (!isTemplate) {
                addEventListeners({ defaultField, fields });
            }

            parent.appendChild(tabs);
            if (errorlist) {
                parent.parentNode.insertBefore(errorlist, parent);
            }
            if (helptext) {
                parent.parentNode.appendChild(helptext);
            }
        }
    });
})();
