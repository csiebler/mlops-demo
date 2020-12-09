# Multi-stage, multi-enviroment Pipelines

This folder contains a typical DEV-to-PROD release pipeline in [`german-credit-rollout.yml`](german-credit-rollout.yml).

This enables the following flow, where a model is trained, tested and deployed in a development environment. Once that has been completed successfully, the same process is repeated in the production environment:

* DEV Stage
  * Train and register model (in DEV environment)
  * Deploy model (in DEV environment)
* PROD Stage (after DEV Stage completed successfully)
  * Train and register model (in PROD environment)
  * Deploy model (in PROD environment)