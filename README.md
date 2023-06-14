# SpectraTrace
SpectraTrace is an audit log service with the ability to store, trace, and analyze a broad spectrum of events, enabling deep insights and comprehensive analysis.

To run the application, please install [docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) on your machine. Then follow one of the following steps to run the application:

1. Using the custom CLI:
```
virtualenv venv
pip install typer
python manage.py start --build
```

2. Using docker compose:
```
docker-compose up --build
```

**Please make sure that you are at the same directory where the `docker-compose.yaml` file is located. (For both of the above approaches)**


### Important

* To view the **design decisions** for this application, view the [`server/docs/README.md`](https://github.com/rifatrakib/SpectraTrace/blob/master/server/docs/README.md) file. ALternatively, run the application using either of the above methods and then visit, `http://127.0.0.1:8000/docs` page to see the explanation.

* To view the **guidelines to test the application using cURL**, please view the [`guidelines.md`](https://github.com/rifatrakib/SpectraTrace/blob/master/guidelines.md) file.
