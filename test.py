from recommender import recommend_colleges

results = recommend_colleges(
    course="B.Tech",
    specialization="Computer",
    location="Delhi",
    max_fee=200000,
    exam="JEE",
)

print(results)
