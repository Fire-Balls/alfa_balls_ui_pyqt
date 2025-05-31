from network.new.client import TaskTrackerClient

client = TaskTrackerClient('http://localhost:8080')
client.login("super123@urfu.ru", "super")

# user = client.get_user(1)
# newproject = client.create_project("p1", "TST")
# client.put_user_in_project(1, newproject.id)
# usernew = client.get_user(1)
# board = client.create_board(newproject.id, "testb")
# projnew = client.get_project(newproject.id)
# issue = client.create_issue(newproject.id, board.id, "task1", "task1desc", 1, 1, "2025-04-30T22:34:45", ["@git"])
#
# boardnew = client.get_board(newproject.id, board.id)
# print(projnew)