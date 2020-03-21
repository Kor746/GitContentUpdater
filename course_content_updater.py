from git import Git, Repo
import os
import sys
from pathlib import Path
import shutil

# python3 -m venv .venv
# source .venv/bin/activate

class Messenger:

	def __init__(self):
		self.messages = {1 : "Cloned {}", 2 : "Added file {} to {}", 3 : "Removed file {} from {}", 4 : "Path {} already exists!", 5 : "No file removed from {}"}

	def getMessage(self, messageType, url, file_name = None):
		if not file_name:
			return self.messages.get(messageType, lambda : "Invalid Message Type!").format(url);
		return self.messages.get(messageType, lambda : "Invalid Message Type!").format(file_name, url);


class MenuInterface:

	def printMenu(self):
		pass;


class CourseContentUpdater(MenuInterface):

		def __init__(self, source_repo_url = "https://github.com/Kor746/SourceTestRepository.git", 
			target_repo_url = "https://github.com/Kor746/TargetTestRepository.git",
			lessons_file_name = "01-Lesson-Plans"):
				self.source_repo_url = source_repo_url
				self.target_repo_url = target_repo_url

				self.source_file_name = os.path.splitext(self.source_repo_url.split("/")[-1])[0]
				self.source_proj_dir = self.getDirPath(self.source_file_name)
				self.source_git_repo = Git(self.source_proj_dir)

				self.target_file_name = os.path.splitext(self.target_repo_url.split("/")[-1])[0]
				self.target_proj_dir = self.getDirPath(self.target_file_name)
				self.target_git_repo = Git(self.target_proj_dir)

				self.seen = None
				self.lessons_file_name = lessons_file_name
				self.messenger = Messenger()

		def run(self):
			self.cloneRepo(self.source_repo_url, self.source_proj_dir, self.source_git_repo)
			self.cloneRepo(self.target_repo_url, self.target_proj_dir, self.target_git_repo)
			choices = {1 : self.addLesson, 2: self.removeLesson, 3 : self.exitProgram}
			
			print()
			while True:
				try:
					self.printMenu()
					choice = int(input("Please enter your choice: ").strip())
					res = choices.get(choice, lambda : "That choice does not exist. Please choose again!")
					print(res())

				except ValueError:
					print("Please enter an integer!")
				print()

		def printMenu(self):
			print("Type 1 to add new course lesson to GitLab.\n" \
		"Type 2 to remove course lesson.\n" \
		"Type 3 to exit the program.");

		def getDirPath(self, file_name):
			base_path = os.path.dirname(os.getcwd())
			return os.path.join(base_path, file_name);

		def isDirEmpty(self, dir_path):
				return not len(os.listdir(dir_path));
 
		def cloneRepo(self, url_path, dir_path, git_obj):
			if not os.path.exists(dir_path):
				print("Creating directory for {}".format(file_name))
				os.mkdir(dir_path)

			if self.isDirEmpty(dir_path):
				print("Empty directory detected! Cloning {}".format(url_path))
				git_obj.clone(url_path)

				print(self.messenger.getMessage(1, url_path))

			print(self.messenger.getMessage(4, url_path))

		def pullRepo(self, repo_path):
			print("Pulling from repository {}".format(repo_path))
			repo = Repo(repo_path)
			repo.git.pull()

		def getRepoPath(self, dir_path):
			return os.path.join(dir_path, os.listdir(dir_path)[1])

		def copyFileToRepo(self, source_path, target_path, target_full_path):
			if os.path.isdir(target_path):
				shutil.copytree(source_path, target_full_path)

		def pushFileToRepo(self, target_repo_path, target_full_path, source_file_name):
			repo = Repo(target_repo_path)
			repo.git.add(target_full_path)
			repo.git.commit("-m", "Committed with updates to {}".format(source_file_name))
			repo.git.push()

		def addLesson(self):
			source_repo_path = self.getRepoPath(self.source_proj_dir)
			target_repo_path = self.getRepoPath(self.target_proj_dir)
			self.pullRepo(source_repo_path)
			self.pullRepo(target_repo_path)
			self.cacheExistingFiles(target_repo_path)

			source_files = sorted(Path(os.path.join(source_repo_path, self.lessons_file_name)).iterdir(), key = os.path.getmtime)
			
			for source_path in source_files:
				source_file_name = os.path.splitext(str(source_path).split("/")[-1])[0]
				if source_file_name not in self.seen:
					target_full_path = os.path.join(target_repo_path, source_file_name)
					self.copyFileToRepo(source_path, target_repo_path, target_full_path)
					self.pushFileToRepo(target_repo_path, target_full_path, source_file_name)
					return self.messenger.getMessage(2, target_repo_path, source_file_name);

		def removeLesson(self):
			target_repo_path = self.getRepoPath(self.target_proj_dir)
			self.pullRepo(target_repo_path)
			self.cacheExistingFiles(target_repo_path)
			file_to_delete = None

			while file_to_delete not in self.seen:
				file_to_delete = input("Enter a valid file name or 0 to exit: ").strip()
				if file_to_delete == "0":
					return self.messenger.getMessage(5, target_repo_path);

			file_to_delete_full_path = os.path.join(target_repo_path, file_to_delete)
			shutil.rmtree(file_to_delete_full_path)
			self.pushFileToRepo(target_repo_path, file_to_delete_full_path, file_to_delete)

			return self.messenger.getMessage(3, target_repo_path, file_to_delete);

		def cacheExistingFiles(self, full_path):
			self.seen = set(os.listdir(full_path))

		def exitProgram(self):
			print("Exiting program...")
			sys.exit(0)


if __name__ == "__main__":
	contentUpdater = CourseContentUpdater()
	contentUpdater.run()
	
