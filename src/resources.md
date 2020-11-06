# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## DesignRuleResult

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/designruleresult)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| rule_type |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| success |  | boolean | nee | ~~C~~​R​~~U~~​~~D~~ |
| errors |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |

## DesignRuleSession

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/designrulesession)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| uuid |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| started_at |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| percentage_score |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| results |  | array | nee | ~~C~~​R​~~U~~​~~D~~ |

## DesignRuleTestSuite

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/designruletestsuite)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| uuid |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| api_endpoint |  | string | ja | C​R​U​D |
| sessions |  | array | nee | ~~C~~​R​~~U~~​~~D~~ |

## DesignRuleTestOption

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/designruletestoption)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| rule_type |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |

## DesignRuleTestVersion

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/designruletestversion)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| id |  | integer | nee | ~~C~~​R​~~U~~​~~D~~ |
| version |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| name |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| test_rules |  | array | nee | ~~C~~​R​~~U~~​~~D~~ |

## ExposedUrl

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/exposedurl)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| id |  | integer | nee | ~~C~~​R​~~U~~​~~D~~ |
| subdomain | The subdomain under which the service has been exposed | string | nee | C​R​U​D |
| session | The session to which this exposed URL belongs | integer | ja | C​R​U​D |
| vng_endpoint |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |

## PostmanTest

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/postmantest)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| name | The name of the Postman test suite | string | ja | C​R​U​D |
| version | Indicates the version of the Postman test suite, allowing for different
        versions under the same name
         | string | nee | C​R​U​D |
| test_scenario | The name of the test scenario to which this Postman test is linked | integer | ja | C​R​U​D |
| validation_file |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |

## Endpoint

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/endpoint)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| name | The name of the variable | string | ja | C​R​U​D |
| value | The value of the variable | string | ja | C​R​U​D |

## Environment

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/environment)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| name | The name of this environment | string | ja | C​R​U​D |
| uuid | The universally unique identifier of this environment | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| endpoints |  | array | nee | C​R​U​D |

## ServerRun

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/serverrun)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| uuid | The universally unique identifier of this provider run, needed to retrieve the badge | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| test_scenario |  | string | ja | C​R​U​D |
| started | The time at which the provider run was started | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| stopped | The time at which the provider run was stopped | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| build_version |  | string | nee | C​R​U​D |
| client_id | If the test scenario requires JWT authentication, this field will be used to construct a JWT | string | nee | C​R​U​D |
| secret | If the test scenario requires JWT authentication, this field will be used to construct a JWT | string | nee | C​R​U​D |
| status | Indicates the status of this provider run | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| percentage_exec | Indicates what percentage of the provider run has been executed | integer | nee | C​R​U​D |
| status_exec | Indicates the status of execution of the provider run | string | nee | C​R​U​D |

## Session

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/session)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| uuid | The universally unique identifier of this session, needed to retrieve the badge | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| session_type |  | string | ja | C​R​U​D |
| started | The time at which the session was started | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| stopped | The time at which the session was stopped | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| status | Indicates the status of this session | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| exposedurl_set |  | array | nee | ~~C~~​R​~~U~~​~~D~~ |
| build_version |  | string | nee | C​R​U​D |
| sandbox | If enabled, whenever multiple calls are made to the same path, the result of the call is overridden every time | boolean | nee | C​R​U​D |

## ScenarioCase

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/scenariocase)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url | 
    URL pattern that will be compared
    with the request and eventually matched.
    Wildcards can be added, e.g. &#39;/test/{uuid}/stop&#39;
    will match the URL &#39;/test/c5429dcc-6955-4e22-9832-08d52205f633/stop&#39;.
     | string | ja | C​R​U​D |
| http_method | The HTTP method that must be tested for this scenario case | string | nee | C​R​U​D |
| collection | The collection of scenario cases to which this scenario case belongs | integer | ja | C​R​U​D |


* Create, Read, Update, Delete
