import codecs
from fastapi import FastAPI,Request,UploadFile,File,Form,HTTPException,status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3

import uvicorn
import csv
#coonecting templates
templates = Jinja2Templates(directory="templates")

app=FastAPI()

#Create a connection to  SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create a Users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL
    )
''')
conn.commit()


@app.get("/", response_class=HTMLResponse)
def new(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})




@app.post("/result")
async def upload_file(request: Request, file: UploadFile = File(...), name_col: int = Form(...), age_col: int = Form(...)):
    try:
        contents= await file.read() #file reading witn await
        data=contents.decode("utf-8")  #convert byte into string using utf-8
        files=csv.DictReader(data.splitlines())
        
        for i in files:
            name=i[list(i.keys())[name_col-1]]#to get the list of name values
            
            age=i[list(i.keys())[age_col-1]]#to get the list of age values
       
            cursor.execute('''
                INSERT INTO Users (name, age)
                VALUES (?, ?)
                 ''', (name, age))
            conn.commit() #to save the changes

    except:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='There was an error uploading the file',
        )       
    finally:
        await file.close()
    return {'message': f'Successfuly uploaded {file.filename}'}


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True)


