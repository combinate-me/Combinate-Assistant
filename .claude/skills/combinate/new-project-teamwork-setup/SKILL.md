---
name: new-project-setup
description: Sets up a new Insites project in Teamwork by copying the standard tasklists (Account Management, Project Management, Discovery, Documentation, Infrastructure, and WBxx template) from the master template project. Trigger on "new project setup", "set up new project", "copy template tasklists", or when a new Teamwork project has been created and needs its standard tasklists.
model: claude-sonnet-4-6
---

# Skill: New Project Setup

Copies the standard Combinate tasklists from the master template project into a freshly created Teamwork project. This is a standard Insites project setup.

## When to Use

- A new Teamwork project has been created and needs its standard tasklists
- "Set up the new project"
- "Copy template tasklists to [project]"

---

## Inputs Required

- **New project URL** - e.g. `https://pm.cbo.me/app/projects/437815`
  - Extract the project ID from the URL: `https://pm.cbo.me/app/projects/PROJECT_ID`

---

## Template Project

- **Template project ID:** `348395`
- **Template project URL:** `https://pm.cbo.me/app/projects/348395`

### Standard Tasklists to Copy

| Tasklist Name | Template ID |
|---------------|-------------|
| Account Management | 1319412 |
| Project Management | 1319411 |
| Discovery | 1319414 |
| Documentation | 1319415 |
| Infrastructure, Environments and Insites setup | 1395790 |
| **WB[xx] - Work Block Name | 1319425 |

---

## Copy Workflow

### Important: Teamwork has no built-in copy API

The Teamwork API does not support direct tasklist copying. The workflow below recreates tasklists and all their tasks (including multi-level subtasks) via the API.

### Step 1 - Get new project ID

Extract the project ID from the URL provided:
- `https://pm.cbo.me/app/projects/437815` → project ID is `437815`

### Step 2 - Run the copy script

Use this Python script. Inject `TEAMWORK_API_KEY` directly from the environment (do NOT use `open('.env')` in a heredoc context - it won't resolve the path correctly).

```bash
source .env && python3 -c "
import subprocess, json, time

KEY = '$TEAMWORK_API_KEY'
SITE = 'https://pm.cbo.me'
NEW_PROJECT_ID = NEW_PROJECT_ID_HERE  # Replace with actual ID

TEMPLATE_TASKLISTS = [
    (1319412, 'Account Management'),
    (1319411, 'Project Management'),
    (1319414, 'Discovery'),
    (1319415, 'Documentation'),
    (1395790, 'Infrastructure, Environments and Insites setup'),
    (1319425, '**WB[xx] - Work Block Name'),
]

def api_get(path):
    r = subprocess.run(['curl', '-s', '-u', KEY+':x', SITE+path],
                       capture_output=True, text=True)
    return json.loads(r.stdout)

def api_post(path, body):
    r = subprocess.run(['curl', '-s', '-X', 'POST', '-u', KEY+':x',
                        '-H', 'Content-Type: application/json',
                        '-d', json.dumps(body), SITE+path],
                       capture_output=True, text=True)
    return json.loads(r.stdout)

def create_tasklist(project_id, name):
    result = api_post(f'/projects/{project_id}/tasklists.json',
                      {'tasklist': {'name': name}})
    tl_id = result.get('TASKLISTID')
    if tl_id:
        print(f'  Created tasklist: {name} -> {tl_id}')
    else:
        print(f'  ERROR creating tasklist {name}: {result}')
    return tl_id

for tmpl_tl_id, tl_name in TEMPLATE_TASKLISTS:
    print(f'\n--- {tl_name} ---')
    new_tl_id = create_tasklist(NEW_PROJECT_ID, tl_name)
    if not new_tl_id:
        continue

    tmpl_tasks = api_get(f'/tasklists/{tmpl_tl_id}/tasks.json?includeCompletedTasks=false').get('todo-items', [])

    # Create top-level tasks first
    id_map = {}
    for task in [t for t in tmpl_tasks if not t.get('parentTaskId') or t['parentTaskId'] == '']:
        item = {'content': task['content'], 'description': task.get('description', '')}
        if task.get('responsible-party-id', '').strip():
            item['responsible-party-id'] = task['responsible-party-id'].strip()
        result = api_post(f'/tasklists/{new_tl_id}/tasks.json', {'todo-item': item})
        new_id = result.get('id') or result.get('TASKID')
        if new_id:
            id_map[int(task['id'])] = int(new_id)
            print(f'  [L1] {task[\"content\"][:60]}')
        time.sleep(0.1)

    # Create subtasks in passes (handles multi-level nesting)
    for level in range(1, 6):
        pending = [t for t in tmpl_tasks
                   if t.get('parentTaskId') and t['parentTaskId'] != ''
                   and int(t['id']) not in id_map
                   and int(t['parentTaskId']) in id_map]
        if not pending:
            break
        for task in pending:
            new_parent = id_map[int(task['parentTaskId'])]
            item = {
                'content': task['content'],
                'description': task.get('description', ''),
                'parentTaskId': str(new_parent)
            }
            if task.get('responsible-party-id', '').strip():
                item['responsible-party-id'] = task['responsible-party-id'].strip()
            result = api_post(f'/tasklists/{new_tl_id}/tasks.json', {'todo-item': item})
            new_id = result.get('id') or result.get('TASKID')
            if new_id:
                id_map[int(task['id'])] = int(new_id)
                print(f'    [L{level+1}] {task[\"content\"][:60]}')
            time.sleep(0.1)

    print(f'  Done: {len(id_map)}/{len(tmpl_tasks)} tasks')

print('\nAll tasklists created.')
"
```

### Step 3 - Verify

Check the new project in Teamwork to confirm all 6 tasklists appear with their tasks.

Expected task counts:
| Tasklist | Tasks |
|----------|-------|
| Account Management | 14 (13 top + 1 sub) |
| Project Management | 13 (8 top + 5 sub) |
| Discovery | 4 (top-level only) |
| Documentation | 27 (15 top + 12 sub) |
| Infrastructure | 21 (6 top + 15 sub) |
| WBxx Template | 38 (5 top + 33 sub) |

---

## Notes

- The `**WB[xx] - Work Block Name` tasklist is the template for each work block. Rename and duplicate it as needed for the project.
- The template project (348395) is the source of truth. If tasks are added to the template in future, re-run this skill for new projects.
- Teamwork rate limits API calls - the `time.sleep(0.1)` between requests avoids hitting limits on large tasklists.
- The WBxx template has 5 levels of nesting - the script handles up to 6 passes to ensure all are captured.
