import pickle, json, os
from datetime import datetime

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


def train_model():
    print("Загрузка набора данных Iris...")
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.3, random_state=42
    )
    
    print("Обучение модели Random Forest...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    print("Оценка модели...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Точность модели: {accuracy:.4f}")
    print("\nОтчёт классификации:")
    print(classification_report(y_test, y_pred, target_names=iris.target_names))
    
    output_dir = "/app/models"
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, "iris_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"Модель сохранена: {model_path}")
    
    metrics = {
        "accuracy": float(accuracy),
        "n_samples_train": len(X_train),
        "n_samples_test": len(X_test),
        "timestamp": datetime.now().isoformat()
    }
    
    metrics_path = os.path.join(output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Метрики сохранены: {metrics_path}")

if __name__ == "__main__":
    train_model()