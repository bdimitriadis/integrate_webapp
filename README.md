# INTEGRATE web application
Online digital tools are considered an innovative method to promote HIV, hepatitis and STIs prevention, testing and treatment services, overcoming individual and social barriers, especially for younger people and other, possibly hard-to-reach, target population groups. INTEGRATE RiskRadar webapp is a web application developed in the scope of the EU-supported INTEGRATE Joint Action (JA), that aims to enhance the integration of combination prevention, testing and linkage to care for HIV, hepatitis, STIs and tuberculosis by providing integrated information and digital tools regarding all four diseases to population groups at increased risk, aiming to eliminate the individual and social barriers to effective adoption of prevention practices, testing and linkage to care, and thus reduce the incidence and burden of these diseases in the European Region.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

- INTEGRATE backend services must be running on a server:
https://github.com/bdimitriadis/integrate-riskradar-backend

- Partner Notification services must be running on a server:
https://github.com/bdimitriadis/partner-notification

- Things you need to install on your system:

```
* Python 3.x.x (tried with 3.8.13)

* Install necessary python packages via: pip install -r requirements.txt
If not working for older versions of python3, try pip install -r older_requirements.txt
```


## Deployment

Adjust settings in the config.py file to your own system/setup settings.

* Just run app.py in the local directory with python3 on your local machine **for development and testing purposes**.
* To deploy the project **on a live system**, follow the instruction given by the official documentation of flask on http://flask.pocoo.org/docs/0.12/deploying/

## Built With

* [Python 3.8.13](http://www.python.org/) - Developing with the best programming language
* [Flask 2.2.2](http://flask.pocoo.org/) - Flask web development, one drop at a time

## Authors

* **Vlasios Dimitriadis** - *Initial work* - [integrate-webapp](https://github.com/bdimitriadis/integrate_webapp)
