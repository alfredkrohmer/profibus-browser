import connection
import directory

conn = connection.Connection('141.76.82.170', 12345)

d = directory.Directory(conn, 6)
d.read()
print(d.dir_info())