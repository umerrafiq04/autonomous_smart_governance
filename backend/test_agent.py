# from agents.analysis_agent import analyze_complaint

# result = analyze_complaint(
#     title="Road Damage",
#     description="Large pothole causing traffic near hospital."
# )

# print(result)


# from agents.knowledge_agent import generate_guidance

# response = generate_guidance(
#     department="Road Department",
#     issue_type="Road Damage",
#     description="Large pothole causing traffic issues."
# )

# print(response)

# from agents.governance_agent import governance_decision

# result = governance_decision(
#     issue_type="Road Damage",
#     severity="High",
#     department="Road Department",
#     description="Large pothole causing traffic problems."
# )

# print(result)


# from agents.workflow import run_complaint_workflow

# result = run_complaint_workflow(
#     title="Road Damage",
#     description="Large pothole causing traffic near hospital."
# )

# print(result)


from agents.resolution_agent import resolution_decision

result = resolution_decision(
    issue_type="Electricity Issue",
    severity="Critical",
    department="Electricity Department",
    description="Transformer exploded near school.",
    citizen_guidance="Stay away from exposed electrical wires."
)

print(result)