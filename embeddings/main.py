import db
import embedder

def main():
    # text_data = db.fetch_data("col","table")
    
    # combined_text = " ".join(text_data)
    
    vector = embedder.embed_text("Sample text")
    
    print(vector)

    # res = db.save_to_vectordb(vector, "space_id")
    # print("Res:", res)

if __name__ == '__main__':
    main()
