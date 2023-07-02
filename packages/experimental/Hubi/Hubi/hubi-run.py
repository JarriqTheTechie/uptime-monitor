import datetime
import os
import pathlib

from inflection import tableize, camelize, underscore

model_name: str = input("Input Resource Name / singular form").strip()
migration_path = r"C:\Users\jrolle\PycharmProjects\FundShare-saas\src\databases\migrations"
model_path = r"C:\Users\jrolle\PycharmProjects\FundShare-saas\src\application\models"


def create_migration(name=model_name, create=model_name, table=model_name, schema=None, directory=migration_path):
    name = name
    now = datetime.datetime.today()

    if create != None:
        table = create
        stub_file = "create_migration"
    else:
        table = table
        stub_file = "table_migration"

    if table == None:
        table = tableize(name.replace("create_", "").replace("_table", ""))
        stub_file = "create_migration"

    migration_directory = directory
    schema = schema
    schema_source = ""
    if schema is None:
        schema = ""
    else:
        for index, _ in enumerate(schema.split()):
            _args = _.split(":")
            column_name = _args[0]
            column_type = _args[1].lower()
            try:
                line = f"table.{column_type}('{column_name}').{_args[2]}()"
            except IndexError:
                line = f"table.{column_type}('{column_name}')"
            if index == 0:
                schema_source += f"{line}\n"
            else:
                schema_source += f"            {line}\n"

    with open(
            os.path.join(
                pathlib.Path(__file__).parent.absolute(), f"stubs/{stub_file}.stub"
            )
    ) as fp:
        output = fp.read()
        output = output.replace("__MIGRATION_NAME__", camelize(name))
        output = output.replace("__TABLE_NAME__", table)
        output = output.replace("SCHEMA", schema_source)

    file_name = f"{now.strftime('%Y_%m_%d_%H%M%S')}_{name}.py"

    with open(os.path.join(os.getcwd(), migration_directory, file_name), "w") as fp:
        fp.write(output)

    print(
        f"Migration file created: {os.path.join(migration_directory, file_name)}"
    )

def create_model(name=model_name, directory=model_path):
    name = name

    model_directory = directory

    with open(
        os.path.join(pathlib.Path(__file__).parent.absolute(), f"stubs/model.stub")
    ) as fp:
        output = fp.read()
        output = output.replace("__CLASS__", camelize(name))


    file_name = f"{camelize(name)}.py"

    full_directory_path = os.path.join(os.getcwd(), model_directory)

    if os.path.exists(os.path.join(full_directory_path, file_name)):
        print(
            f'<error>Model "{name}" Already Exists ({full_directory_path}/{file_name})</error>'
        )
        return

    os.makedirs(os.path.dirname(os.path.join(full_directory_path)), exist_ok=True)

    with open(os.path.join(os.getcwd(), model_directory, file_name), "w+") as fp:
        fp.write(output)

    print(f"Model created: {os.path.join(model_directory, file_name)}")

create_migration(schema="name:string:unique password:string")
create_model(directory=model_path)