from app import create_app
from extensions import db
from models import NetworkPerformance

app = create_app()

with app.app_context():

    db.create_all()

    donnees = [
        {
            "year": 2022,
            "rendement_adduction": 85.9,
            "rendement_distribution": 76.8,
            "fuites_reparees": 220266,
            "casses_reparees": 22978,
            "incidents_par_km": 4.2,
        },
        {
            "year": 2023,
            "rendement_adduction": 86.8,
            "rendement_distribution": 77.7,
            "fuites_reparees": 209090,
            "casses_reparees": 22191,
            "incidents_par_km": 4.0,
        },
    ]

    source = (
        "Rapport de synthèse statistique SONEDE 2023, page 3"
    )

    for ligne in donnees:
        record = NetworkPerformance.query.filter_by(
            year=ligne["year"]
        ).first()

        if record is None:
            record = NetworkPerformance(**ligne, source=source)
            db.session.add(record)
        else:
            for key, value in ligne.items():
                setattr(record, key, value)
            record.source = source

    db.session.commit()

    print("DONNEES SONEDE AJOUTEES AVEC SUCCES !")
    print("Nombre d'années :", NetworkPerformance.query.count())