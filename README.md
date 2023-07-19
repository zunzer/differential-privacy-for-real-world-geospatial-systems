# Differential Privacy for real world Geospatial Systems

The widespread use of internet-connected devices has led to the generation of vast amounts of geospatial data. However, privacy regulations, such as the General Data Protection Reg-
ulation (GDPR), limit the collection and processing of personal
data. This paper outlines the foundations for the implementation
of differential privacy, a mathematical definition of privacy that
guarantees the protection of individual-level information, while
still enabling privacy-preserving analysis of geospatial data. The
goal is to develop a prototype extension that incorporates a
differentially private mechanism, allowing organizations to collect
and analyze geospatial data while adhering to privacy regulations.
The paper presents the system architecture and methodology
for enabling differential privacy on geospatial data, including
privacy budget establishment, aggregation and generalization,
location perturbation, privacy analysis, and utility considerations.
The proposed extension is implemented using PostgreSQL and
PostGIS, and open-source libraries for differential privacy. The
performance and usability of the implementation are assessed on
using a real geospatial dataset related to food delivery prefer-
ences. The report concludes with a discussion about challenges
and limitations of the proposed approach.

This implementation was realized as part of a project in the course "Privacy Engineering" at the Technical University of Berlin. 

## Requirements

See the included `requirements.txt` or `environment.yaml` files. Python 3.9 or greater is required. 

## Usage 

To run the dashboard web app, run the following command. Ensure that the required dependecies are available. 
```
python GeoClient/app.py
```

The application will start a web server running on localhost. To access it, follow this URL: [localhost:8050](localhost:8050).
If this does not work, see the console output of the application for the correct URL. 