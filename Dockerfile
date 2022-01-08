FROM python:3.9 AS base

ENV PYTHOUNBUFFERED 1
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS python-deps
RUN pip install pipenv
RUN  && apt-get install -y --no-install-recommends gcc
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install

FROM base AS runtime

COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

RUN useradd --create-home appuser

RUN sudo apt-get install nginx

COPY demo.dglte.net /etc/nginx/sites-available/
WORKDIR /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/demo.dglte.net
COPY demo.dglte.net /etc/nginx/sites-enabled/

WORKDIR /
COPY ultima_tea ultima_tea

WORKDIR /ultima_tea
CMD echo yes | python manage.py collectstatic --no-default-ignore && ls -al && gunicorn --bind=0.0.0.0:8080 ultima_tea.wsgi:application
#CMD ls ultima_tea -al & python /ultima_tea/manage.py runserver 0.0.0.0:8000
#CMD ls ultima_tea -al
