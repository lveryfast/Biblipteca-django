Primero se crea el entorno vitual con el comando py -m venv .venv 
Segundo se actuva con el comando venv\Scripts\activate
Tercero se instalan las dependencias necesarias 
pip install --upgrade pip
pip install -r requirements.txt
Cuarto se copia el repositorio para ejecutarlo con el entorno previamente instalado
python manage.py runserver