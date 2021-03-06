include docker/.env

BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Install dev environment
#-----------------------------------------------------------------------------

install:
	@ echo "$(BUILD_PRINT)Installing the production requirements"
	@ pip install --upgrade pip
	@ pip install -r requirements/dev.txt

#-----------------------------------------------------------------------------
# Service commands
#-----------------------------------------------------------------------------
build-volumes:
	@ docker volume create rdf-differ-template

build-services:
	@ echo -e '$(BUILD_PRINT)Building the RDF Differ micro-services'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env build

start-services:
	@ echo -e '$(BUILD_PRINT)Starting the RDF Differ micro-services'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env up -d

stop-services:
	@ echo -e '$(BUILD_PRINT)Stopping the dev services'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env stop


#-----------------------------------------------------------------------------
# Fuseki control for github actions
#-----------------------------------------------------------------------------
build-test-fuseki: | build-volumes
	@ echo -e '$(BUILD_PRINT)Building the Fuseki service'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env build fuseki

start-test-fuseki:
	@ echo -e '$(BUILD_PRINT)Starting the Fuseki service'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env up -d fuseki

#-----------------------------------------------------------------------------
# Test commands
#-----------------------------------------------------------------------------

fuseki-create-test-dbs: | build-test-fuseki start-test-fuseki
	@ echo "$(BUILD_PRINT)Building dummy "subdiv" and "abc" datasets at http://localhost:$(if $(RDF_DIFFER_FUSEKI_PORT),$(RDF_DIFFER_FUSEKI_PORT),unknown port)/$$/datasets"
	@ sleep 5
	@ curl --anyauth --user 'admin:admin' -d 'dbType=mem&dbName=subdiv'  'http://localhost:$(RDF_DIFFER_FUSEKI_PORT)/$$/datasets'
	@ curl --anyauth --user 'admin:admin' -d 'dbType=mem&dbName=abc'  'http://localhost:$(RDF_DIFFER_FUSEKI_PORT)/$$/datasets'

test:
	@ echo "$(BUILD_PRINT)Running the tests"
	@ pytest

lint:
	@ echo "$(BUILD_PRINT)Linting the code"
	@ flake8 || true

#-----------------------------------------------------------------------------
# Template commands
#-----------------------------------------------------------------------------

set-report-template:
	@ echo "$(BUILD_PRINT)Copying custom template"
	@ docker rm temp | true
	@ docker volume rm rdf-differ-template | true
	@ docker volume create rdf-differ-template
	@ docker container create --name temp -v rdf-differ-template:/data busybox
	@ docker cp $(location). temp:/data
	@ docker rm temp

#-----------------------------------------------------------------------------
# Run UI dev environment
#-----------------------------------------------------------------------------

run-ui-dev:
	@ export FLASK_APP=rdf_differ.entrypoints.ui.run
	@ export FLASK_ENV=development
	@ flask run

#-----------------------------------------------------------------------------
# Gherkin feature and acceptance test generation commands
#-----------------------------------------------------------------------------

FEATURES_FOLDER = tests/features
STEPS_FOLDER = tests/steps
FEATURE_FILES := $(wildcard $(FEATURES_FOLDER)/*.feature)
EXISTENT_TEST_FILES = $(wildcard $(STEPS_FOLDER)/*.py)
HYPOTHETICAL_TEST_FILES :=  $(addprefix $(STEPS_FOLDER)/test_, $(notdir $(FEATURE_FILES:.feature=.py)))
TEST_FILES := $(filter-out $(EXISTENT_TEST_FILES),$(HYPOTHETICAL_TEST_FILES))

generate-tests-from-features: $(TEST_FILES)
	@ echo "$(BUILD_PRINT)The following test files should be generated: $(TEST_FILES)"
	@ echo "$(BUILD_PRINT)Done generating missing feature files"
	@ echo "$(BUILD_PRINT)Verifying if there are any missing step implementations"
	@ py.test --generate-missing --feature $(FEATURES_FOLDER)

$(addprefix $(STEPS_FOLDER)/test_, $(notdir $(STEPS_FOLDER)/%.py)): $(FEATURES_FOLDER)/%.feature
	@ echo "$(BUILD_PRINT)Generating the testfile "$@"  from "$<" feature file"
	@ pytest-bdd generate $< > $@
	@ sed -i  's|features|../features|' $@


