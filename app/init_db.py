from app.db import Base, engine
from app.models.match import Match
from app.models.feature import MatchFeature
from app.models.prediction import Prediction
from app.models.prediction_result import PredictionResult


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tables created")


if __name__ == "__main__":
    main()
