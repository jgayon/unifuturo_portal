from database import execute_query

ofertas = execute_query(
    '''SELECT id_oferta, periodo_academico, titulo_conduce, P.nombre AS programa_nombre
       FROM "Oferta" O
       JOIN "Programa" P ON O.id_programa = P.id_programa
       WHERE activa = 'S'
       ORDER BY periodo_academico DESC''',
    fetchall=True
)

print("Ofertas activas encontradas:")
for o in ofertas:
    print(o)