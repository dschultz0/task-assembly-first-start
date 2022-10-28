# Task Assembly First Start
The following are the instructions for getting started quickly with Task Assembly. For this quick
start we've included a very simple task that asks MTurk Workers to write out a number as text.
This is obviously very simple but it will make it easy to test and validate the results as an
example.

## Initial Setup
First, update the `api-key.txt` file with the id that has been provided
by the Task Assembly team. You can just replace `<api-key>` with your id.

Next, we'll need to create a task-type for this project. This is just a placeholder and will be removed from
future updates to Task Assembly. Simply run the following command and capture the id that is generated.

```shell
python -m assembly-client create_task_type NumbersExample
```

Finally, we'll want to create a new Task Definition for our task using the Task Type created in the previous step:

```shell
python -m assembly-client create_task_definition Numbers <task_type_id>
```

This will generate a new definition for our project and write a definition.json file that we will use to capture
our task attributes.

## Build the Task Definition
Now we can update the `definition.json` file with the appropriate attributes for our task. We've included
the core attributes for our task below:

```json
{
    "DefinitionId": "<your_definition_id>",
    "TaskType": "<your_task_type_id>",
    "Title": "Convert number to text",
    "Description": "Write out a number as text",
    "RewardCents": 10,
    "Lifetime": 3600,
    "AssignmentDuration": 300,
    "DefaultAssignments": 2,
    "MaxAssignments": 5,
    "AutoApprovalDelay": 0
}
```

You can now run the following command to update the definition in Task Assembly:

```shell
python -m assembly-client update_task_definition
```

The task interface for our project is in the `template.html` file and you will note that it uses a very similar 
templating language as Amazon SageMaker Ground Truth and the Amazon MTurk website. In most cases you can simply
copy/paste existing task templates from those tools and update the variable names within the `{{ name }}` values.
To apply this new task template to our definition, we can simply run the following command:

```shell
python -m assembly-client update_task_template template.html
```

These same commands can be used to update your Task Definition as you need.

## Create a task in the sandbox
Now that we've completed the setup for our task, we should start by creating a test task in the *Sandbox* environment.
The Sandbox is a mirror of the Production environment but no money changes hands and work isn't generally completed
unless you do it yourself. This is a great way to validate that your task is set up correctly before putting it in the
hands of *real* Workers.

Note: The MTurk Sandbox is distinct from the Production environment so you will want to create a new account at
https://requestersandbox.mturk.com with the same email address as your Production account and also link it to the same
AWS account.

To create a single MTurk task in the Sandbox, you can use the following command. The `--sandbox` flag lets Task
Assembly know to create the task in the appropriate environment and the `--assignments 1` flag indicates that we
only need to ask one Worker to provide an answer to the task (just you). Finally, `number=4` provides the input
data to our task interface which refers to `{{ number }}` from the html template.

```shell
python -m assembly-client create_task --sandbox --assignments 1 number=4
```

Take note of the task ID that is returned. You'll need that to retrieve the results.

This will create a new task for you in the Worker Sandbox, which you can view and work on by visiting
https://workersandbox.mturk.com. You'll likely need to create an account there, feel free to use your personal 
Amazon account or any other account you wish. Once you're logged in, you can search for your username or
"Convert number to text". Then you can accept and complete the task.

After you've completed your task, give MTurk and Task Assembly a few moments to process the result. Then run 
the following to get the output.

```shell
python -m assembly-client get_task 46oogdouhi
```

## Create a *real* task
Now we can repeat the same process to create a task in the Production environment by simply removing the
`--sandbox` and `--assignments` flags.

```shell
python -m assembly-client create_task number=4
```

The same `get_task` command can be used to retrieve results of the created task.


