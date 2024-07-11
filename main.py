import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from py2neo import Graph, Node, Relationship
import os
from dotenv import dotenv_values

config = dotenv_values(".env")
api_key = config["OPENAI_API_KEY"]
org_id = config["OPENAI_ORG_ID"]
graph_user = config["NEO4J_USER"]
graph_pass = config["NEO4J_PASS"]
graph_server_url = "neo4j+s://029d4dd6.databases.neo4j.io"

kernel = sk.Kernel()
kernel.add_chat_service("chat-gpt", OpenAIChatCompletion("gpt-4-1106-preview", api_key, org_id))
skills_directory = "assets/skills"
callCenterSkills = kernel.import_semantic_skill_from_directory(skills_directory, "callCenterSkill")

CustomerName = callCenterSkills["CustomerName"]
CustomerSentiment = callCenterSkills["CustomerSentiment"]
OperatorSentiment = callCenterSkills["OperatorSentiment"]
Product = callCenterSkills["Product"]
IssueResolved = callCenterSkills["IssueResolved"]
OperatorProficiency = callCenterSkills["OperatorProficiency"]
ProductIssue = callCenterSkills["ProductIssue"]

graph = Graph(graph_server_url, auth=(graph_user, graph_pass))

# Clear the database if needed
graph.delete_all()

directory = 'assets/transcriptions/complaints'
for dirpath, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        with open(os.path.join(dirpath, filename), 'r') as f:
            transcript = f.read()

            product = Product(transcript).result
            productIssue = ProductIssue(transcript).result
            customerSentiment = CustomerSentiment(transcript).result
            operatorSentiment = OperatorSentiment(transcript).result
            operatorProficiency = OperatorProficiency(transcript).result
            issueResolved = IssueResolved(transcript).result
            customerName = CustomerName(transcript).result

            print(product)
            print("====================================")
            print(productIssue)
            print("====================================")
            print(customerSentiment)
            print("====================================")
            print(operatorSentiment)
            print("====================================")
            print(operatorProficiency)
            print("====================================")
            print(issueResolved)
            print("====================================")
            print(customerName)

            callNode = Node("Customer Call")
            productNode = Node("Product", product=product)
            productIssueNode = Node("Issue", issue=productIssue)
            customerSentimentNode = Node("Customer_Sentiment" , sentiment=customerSentiment)
            operatorSentimentNode = Node("Operator_Sentiment" , sentiment=operatorSentiment)
            operatorProficiencyNode = Node("Operator_Proficiency" , proficiency=operatorProficiency)
            callOutcomeNode = Node("Call_Outcome" , resolved=issueResolved)
            operatorNode = Node("Operator", name="Operator")
            customerNode = Node("Customer", name=customerName)

            graph.create(operatorNode)
            graph.create(customerNode)
            graph.create(callNode)
            graph.create(productNode)
            graph.create(productIssueNode)
            graph.create(customerSentimentNode)
            graph.create(operatorSentimentNode)
            graph.create(callOutcomeNode)
            graph.create(operatorProficiencyNode)
            
            graph.create(Relationship(callNode, "OPERATOR", operatorNode))
            graph.create(Relationship(callNode, "CUSTOMER", customerNode))
            graph.create(Relationship(callNode, "HAS_PRODUCT", productNode))
            graph.create(Relationship(callNode, "HAS_ISSUE", productIssueNode))
            graph.create(Relationship(customerNode, "HAS_SENTIMENT", customerSentimentNode))
            graph.create(Relationship(operatorNode, "HAS_SENTIMENT", operatorSentimentNode))
            graph.create(Relationship(callNode, "HAD_OUTCOME", callOutcomeNode))
            graph.create(Relationship(operatorNode, "PROFICIENCY_RATING", operatorProficiencyNode))