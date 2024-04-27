class UnstructuredDb():
    def __init__(self,path:str="db/",table:str='ingredients'):
        import chromadb
        import os
        from chromadb.db.base import UniqueConstraintError
        from chromadb.utils import embedding_functions
        
        if not os.path.exists(path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"Directory '{dir_path}' created successfully.")

         
        
        client = chromadb.PersistentClient(path=path)
        em = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="Huffon/sentence-klue-roberta-base")
        try:
            self.collection = client.create_collection(name=table, embedding_function=em)
        except UniqueConstraintError: 
            self.collection = client.get_collection(name=table, embedding_function=em)
            
    def get(self,text:str,n:int=2)->[str]:
        
        text=self.sort_ingredients(text)
        results=self.collection.query(query_texts=[text],n_results=n)
        urls=[f"https://www.10000recipe.com/recipe/{id}" for id in results['ids'][0]]

        return urls
        
    def sort_ingredients(self,ingredient_str:str)->str:
        if ingredient_str=="":
            return ingredient_str
        ingredients_list = ingredient_str.split(',') 
        ingredients_list.sort() 
        return ', '.join(ingredients_list)

    def add(self,key:str=None,ingredient:str=None,metadata:dict=None):
        ingredient=sort_ingredients(ingredient)
        self.collection.add(
        documents=[ingredient],
        metadatas=[metadata],
        ids=[key]
        )


from flask import Flask, request

app = Flask(__name__)  

db = UnstructuredDb()  

@app.route('/search/<int:n>', methods=['GET'])  
def search(n):
    text = request.args.get('text')
    return db.get(text=text,n=n)

if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=9999)
