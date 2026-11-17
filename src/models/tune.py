from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def tune_model(model_name, model, X, y, cv):
    if model_name == "LinearRegression":
        estimator = model if isinstance(model, Pipeline) else Pipeline(
            [("scale", StandardScaler()), ("model", LinearRegression())]
        )
        grid = {"model__fit_intercept": [True, False]}
    elif model_name == "DecisionTreeRegressor":
        estimator = model
        prefix = "model__" if isinstance(model, Pipeline) else ""
        grid = {f"{prefix}max_depth": [2, 4, 6, None], f"{prefix}min_samples_leaf": [1, 3, 5]}
    elif model_name == "RandomForestRegressor":
        estimator = model
        prefix = "model__" if isinstance(model, Pipeline) else ""
        grid = {
            f"{prefix}n_estimators": [100, 200],
            f"{prefix}max_depth": [None, 5, 10],
            f"{prefix}min_samples_leaf": [1, 3],
        }
    elif isinstance(model, HistGradientBoostingRegressor) or (
        isinstance(model, Pipeline)
        and any(isinstance(step, HistGradientBoostingRegressor) for step in model.named_steps.values())
    ):
        estimator = model
        prefix = "model__" if isinstance(model, Pipeline) else ""
        grid = {
            f"{prefix}max_iter": [100, 200],
            f"{prefix}learning_rate": [0.05, 0.1],
            f"{prefix}max_leaf_nodes": [7, 15, 31],
            f"{prefix}l2_regularization": [0.0, 1.0],
        }
    else:
        estimator = model
        grid = {}
    search = GridSearchCV(
        estimator, grid, cv=cv, scoring="neg_mean_absolute_error",
        n_jobs=1, refit=True, error_score="raise",
    )
    search.fit(X, y)
    return search.best_estimator_, {
        "best_params": search.best_params_,
        "best_cv_mae": float(-search.best_score_),
        "grid_candidates": int(len(search.cv_results_["params"])),
    }
