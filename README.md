# confluence-audit

Audit for confluence

# Example

## Precondition (confluence)

### Users and groups

* developer (group)
  - developer1
  - developer2
  - developer3
* tester (group)
  - tester1
  - tester2

### Spaces and permissions

#### developer-only-space (DEV)

* user
  * tester1 (**invalid!!**)
  * tester2 (**invalid!!**)
* group
  * developer

#### tester-only-space (TEST)

* user
  * tester1
  * tester2
* group
  * developer (**invalid!!**)

#### public-space (PUBLIC)

* user
  * developer1
  * developer2
  * developer3
  * tester1
  * tester2
* group
  * developer
  * tester (**invalid!!**)

## Create `config.yaml`

```yaml
base_url: 'http://your-confluence-path/8090'
deny:
  # tester group is never assigned
  - group_names:
      - tester
  # testers are never assigned to DEV
  - join_group_names:
      - tester
    excepts:
      - TEST
      - PUBLIC
  # developer group and developers are never assigned to TEST
  - group_names:
      - developer
    join_group_names:
      - developer
    excepts:
      - DEV
      - PUBLIC
```

## Set environmental variables

* USER
  - Confluence user name
* PASSWORD
  - Confluence password

## Usage

```
$ confluence_audit --config config.yaml
```

then you will get as following...

```
[
    {
        "group_names": [],
        "space": "DEV",
        "user_names": [
            "tester1",
            "tester2"
        ]
    },
    {
        "group_names": [
            "tester"
        ],
        "space": "PUBLIC",
        "user_names": []
    },
    {
        "group_names": [
            "developer"
        ],
        "space": "TEST",
        "user_names": []
    }
]
```
