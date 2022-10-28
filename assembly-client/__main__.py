import json
import posixpath

import larry as lry
import argparse
import csv
from . import AssemblyClient, REV_TASK_DEFINITION_ARG_MAP


parser = argparse.ArgumentParser("Task Assembly CLI")
subparsers = parser.add_subparsers(dest="command", required=True)

ctt_parser = subparsers.add_parser("create_task_type")
ctt_parser.add_argument("name")

ctd_parser = subparsers.add_parser("create_task_definition")
ctd_parser.add_argument("name")
ctd_parser.add_argument("task_type_id")

utd_parser = subparsers.add_parser("update_task_definition")
utd_parser.add_argument("--definition_file", default="definition.json")

gtd_parser = subparsers.add_parser("get_task_definition")
gtd_parser.add_argument("id")

utt_parser = subparsers.add_parser("update_task_template")
utt_parser.add_argument("template")
utt_parser.add_argument("--definition_file", default="definition.json")

uga_parser = subparsers.add_parser("update_gold_answers")
uga_parser.add_argument("answer_file")
uga_parser.add_argument("--definition_file", default="definition.json")

ct_parser = subparsers.add_parser("create_task")
ct_parser.add_argument("values", type=str, nargs="*")
ct_parser.add_argument("--assignments", type=int)
ct_parser.add_argument("--sandbox", action="store_true")
ct_parser.add_argument("--definition_file", default="definition.json")

gt_parser = subparsers.add_parser("get_task")
gt_parser.add_argument("task_id")
gt_parser.add_argument("--include_assignments", action="store_true")

sb_parser = subparsers.add_parser("submit_batch")
sb_parser.add_argument("--definition_file", default="definition.json")
sb_parser.add_argument("--sandbox", action="store_true")
sb_parser.add_argument("name")
sb_parser.add_argument("input_file")
sb_parser.add_argument("s3_uri_prefix")

args = parser.parse_args()

with open("api-key.txt") as fp:
    client = AssemblyClient(fp.read().strip())


def read_definition(file_name):
    with open(file_name) as ffp:
        definition_ = json.load(ffp)
    return definition_


if args.command == "create_task_type":
    task_type_id = client.create_task_type(args.name)
    print(f"Created task type ID: {task_type_id}")
elif args.command == "create_task_definition":
    definition = client.create_task_definition(args.name, args.task_type_id)
    definition["TaskType"] = args.task_type_id
    with open("definition.json", "w") as fp:
        json.dump(definition, fp, indent=4)
    print(f"Created task definition {definition['DefinitionId']} in definition.json")
elif args.command == "update_task_definition":
    definition = read_definition(args.definition_file)
    params = {REV_TASK_DEFINITION_ARG_MAP[k]: v for k, v in definition.items()}
    client.update_task_definition(**params)
    print(f"Updated task definition {definition['DefinitionId']}")
elif args.command == "get_task_definition":
    definition = client.get_task_definition(args.id)
    if "GoldAnswers" in definition:
        definition.pop("GoldAnswers")
    print(json.dumps(definition, indent=4))
elif args.command == "update_task_template":
    definition = read_definition(args.definition_file)
    with open(args.template) as fp:
        client.update_task_definition(definition["DefinitionId"], template=fp)
    print("Your template has been updated")
elif args.command == "update_gold_answers":
    definition = read_definition(args.definition_file)
    with open(args.answer_file) as fp:
        answers = json.load(fp)
    client.update_task_definition(definition["DefinitionId"], gold_answers=answers)
    print("Your gold answers set has been updated")
elif args.command == "create_task":
    definition = read_definition(args.definition_file)
    params = {
        "definition_id": definition["DefinitionId"]
    }
    if args.assignments:
        params["default_assignments"] = args.assignments
    if args.sandbox:
        params["sandbox"] = True
    if isinstance(args.values, list):
        vals = [v.split("=") for v in args.values]
        params["data"] = {v[0]: v[1] for v in vals}
    else:
        vals = args.values.split("=")
        params["data"] = {vals[0]: vals[1]}
    task_id = client.create_task(**params)
    print(f"Task created: {task_id}")
elif args.command == "get_task":
    response = client.get_task(args.task_id)
    print(json.dumps(response, indent=4))
elif args.command == "submit_batch":
    definition = read_definition(args.definition_file)
    name = args.name.replace(" ", "_")
    with open(args.input_file) as fp:
        lines = list(csv.DictReader(fp))
    input_uri = posixpath.join(args.s3_uri_prefix, f"{name}.jsonl")
    output_uri = posixpath.join(args.s3_uri_prefix, f"{name}_output.jsonl")
    lry.s3.write_as(lines, [dict], input_uri)
    params = {
        "definition_id": definition["DefinitionId"],
        "name": args.name,
        "input_uri": input_uri,
        "output_uri": output_uri,
    }
    if args.sandbox:
        params["sandbox"] = True
    batch_id = client.submit_batch(**params)
    print(f"A batch with id {batch_id} has been created")
    print(f"Results will be written to {output_uri}")
