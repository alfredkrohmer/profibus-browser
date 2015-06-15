import connection
import directory
import server

conn = connection.Connection('141.76.82.170', 12345)

server.run_server(conn)