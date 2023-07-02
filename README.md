# HubiAdmin

The Admin Model is a core component of the admin panel generator that provides a flexible framework for managing different resources within the admin panel. This documentation provides a detailed understanding of the Admin Model and its associated methods and attributes.

## Class Structure
The Admin Model class serves as a base class for specific admin models, providing a set of common functionalities. It includes the following attributes and methods:


## Attributes
`menu_icon`: Specifies the icon to be displayed for the admin model in the menu. \
`navigation_label`: Specifies the label for the navigation item associated with the admin model. \
`preview_field`: Indicates the field to be used for previewing records. \
`model_label`: Specifies the label for the model.
`table_polling`: Enables or disables table polling for real-time updates. Set it to True to enable table polling or False to disable it. \
`poll_interval`: Specifies the polling interval in seconds. Adjust this value according to your requirements.`

## Header Metrics
The `get_header_metrics()` method allows you to retrieve and render header metrics for the admin model. Use this method to display statistical information or key metrics related to the resource. Customize the implementation of this method to provide meaningful and relevant metrics.

## Fillable Form Fields
The `get_fillable()` method returns a list of form components that are used for creating or editing records. Customize this method to define the form fields specific to the admin model. The form components can include text inputs, checkboxes, dropdowns, or any other relevant form elements.

## Table Columns
The `get_table_columns()` method returns a list of table columns that define the presentation of records in the admin panel. Customize this method to specify the columns that should be displayed for the admin model. Each column can represent a specific attribute or property of the resource. Consider using appropriate column types, such as text columns, numeric columns, boolean columns, or date columns, depending on the nature of the data being displayed.

## Related Resources
The `get_relations()` method allows you to define related resources for the admin model. Use this method to specify any resources that are associated with the current model. For example, if the admin model represents users, related resources could include roles, permissions, or user groups. Customize the implementation of this method to return the appropriate list of related resources.

## Operations Hooks
The Admin Model provides hooks that allow you to perform operations before and after creating or editing records. These hooks enable you to modify or validate data before it is saved, as well as perform any additional actions required after the record is created or edited. Implement the `before_create()`, `after_create()`, `before_edit()`, and `after_edit()` methods to customize the behavior as needed.

## Permissions
The Admin Model includes permission methods that determine user access privileges for various operations related to the admin model. Implement the permission methods such as `can_list()`, `can_view()`, `can_edit()`, `can_create()`, `can_delete()`, `can_export()`, `can_import()`, and `can_filter()` based on your specific authorization requirements. These methods should return True or False based on the user's permissions.

This technical documentation provides a comprehensive understanding of the Admin Model and its functionalities. Refer to this documentation when working with the admin panel generator to effectively manage resources within the admin panel.


### Example Usage

```

class AdminModel:
    menu_icon = ""  # Icon for the admin model in the menu
    navigation_label = ""  # Label for the navigation item
    preview_field = ""  # Field used for previewing records
    model_label = ""  # Label for the model
    table_polling = False  # Enable or disable table polling for real-time updates
    poll_interval = 1  # Polling interval in seconds

    def get_header_metrics(self):
        # Retrieve and render header metrics for the admin model
        pass

    def get_fillable(self):
        # Return a list of form components for creating or editing records
        pass

    def get_table_columns(self):
        # Return a list of table columns to display records
        pass

    def get_relations(self):
        # Return a list of related resources for the admin model
        pass

    def before_create(self, data):
        # Perform operations before creating a record
        return data

    def after_create(self, model):
        # Perform operations after creating a record
        return model

    def before_edit(self, data):
        # Perform operations before editing a record
        return data

    def after_edit(self, model):
        # Perform operations after editing a record
        return model

    # Permissions
    def can_list(self) -> bool:
        # Check if the user has permission to list records
        pass

    def can_view(self) -> bool:
        # Check if the user has permission to view a record
        pass

    def can_edit(self) -> bool:
        # Check if the user has permission to edit a record
        pass

    def can_create(self) -> bool:
        # Check if the user has permission to create a record
        pass

    def can_delete(self) -> bool:
        # Check if the user has permission to delete a record
        pass

    def can_export(self) -> bool:
        # Check if the user has permission to export records
        pass

    def can_import(self) -> bool:
        # Check if the user has permission to import records
        pass

    def can_filter(self) -> bool:
        # Check if the user has permission to filter records
        pass

```
