import sys

sys.stdout.write("USER sagar\r\n")
sys.stdout.write("PASS patel\r\n")
sys.stdout.write("PORT 10,1,1,0,12,255\n")
sys.stdout.write("RETR ls\r\n")
# sys.stdout.write("RETR some_dir/neither_does_this_one\r\n")
# sys.stdout.write("RETR ls\r\n")
# sys.stdout.write("PORT 10,1,1,0,12,255\r\n")
# sys.stdout.write("RETR does_not_exist_hopefully\r\n")