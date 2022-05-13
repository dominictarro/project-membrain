py=`pwd`/venv/bin/python3.10
nltk_data=`pwd`/nltk_data
docker_db_data=`pwd`/.docker_db_data
.DEFAULT_GOAL := build

logs:
	if ! [ -d logs ]; then mkdir logs; fi
nltk:
	if ! [ -d ${nltk_data} ]; then mkdir ${nltk_data}; fi
	${py} -m nltk.downloader -d ${nltk_data} \
		averaged_perceptron_tagger \
		maxent_ne_chunker \
		omw-1.4 \
		punkt \
		stopwords \
		wordnet \
		words
venv:
	python3.10 -m venv venv &&\
	 ${py} -m pip install -r requirements.txt
create-database:
	docker-compose up --no-start db
.env:
	if ! [ -f .env ]; then touch .env; done

build: venv nltk logs create-database
