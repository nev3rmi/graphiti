# Neo4j Browser Queries for Verifying MCP Data

Access Neo4j Browser at: **http://192.168.31.150:7474**

## 1. View All Data Overview
```cypher
MATCH (n) WHERE n.group_id = 'default'
RETURN labels(n) as node_type, count(n) as count
ORDER BY count DESC
```

## 2. View All Episodes (Stories/Conversations)
```cypher
MATCH (e:Episodic) WHERE e.group_id = 'default'
RETURN e.uuid, e.source, e.content, e.created_at
ORDER BY e.created_at DESC
```

## 3. View All Entities (People, Organizations, Projects)
```cypher
MATCH (e:Entity) WHERE e.group_id = 'default'
RETURN e.name, e.summary, e.uuid
ORDER BY e.name
```

## 4. View All Relationships
```cypher
MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity) 
WHERE r.group_id = 'default'
RETURN a.name as from_entity, r.name as relationship_type, 
       b.name as to_entity, r.fact
ORDER BY a.name
```

## 5. Search for Specific Content
```cypher
// Search episodes about machine learning
MATCH (e:Episodic) WHERE e.group_id = 'default'
AND toLower(e.content) CONTAINS 'machine learning'
RETURN e.content, e.source

// Search entities related to TechCorp
MATCH (e:Entity) WHERE e.group_id = 'default'
AND (e.name CONTAINS 'Tech' OR e.summary CONTAINS 'Tech')
RETURN e.name, e.summary

// Find work relationships
MATCH (a)-[r:RELATES_TO]->(b) WHERE r.group_id = 'default'
AND r.name CONTAINS 'work'
RETURN a.name, r.name, b.name, r.fact
```

## 6. Visualize the Knowledge Graph
```cypher
MATCH (n) WHERE n.group_id = 'default'
OPTIONAL MATCH (n)-[r]-(m) WHERE r.group_id = 'default'
RETURN n, r, m
LIMIT 50
```

## Current Data Summary (as of verification):
- **8 Episodes**: Conversations and stories stored by MCP tools
- **4 Entities**: Alice Johnson, Bob Wilson, TechCorp, Project Phoenix  
- **5 Relationships**: Work relationships and collaborations
- **All data searchable**: By content, names, facts, and relationships

## MCP Tool Data Sources:
- `employee_profile`: Alice Johnson's profile
- `new_hire_info`: Bob Wilson's information  
- `project_meeting`: Project Phoenix collaboration
- `mcp_test`: Test episodes from validation
- `mcp_validation`: MCP functionality tests
- `ollama_integration_test`: Ollama integration tests

## How to Use:
1. Open Neo4j Browser at http://192.168.31.150:7474
2. Login with: neo4j / granite-life-bonanza-sunset-lagoon-1071
3. Copy and paste any query above
4. Click "Run" to execute and visualize results