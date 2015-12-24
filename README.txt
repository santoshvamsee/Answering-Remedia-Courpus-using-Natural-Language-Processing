INSTRUCTIONS:
————————————

1. Open terminal at this folder location.
2. Run command - “python solve_remedia.py”


DEPENDENCIES:
————————————

nltk
numpy
PyDictionary
k-parser (output of k-parser is given in folder aspIO)


HOW TO READ LOG FILE:
————————————————————

Search Keywords in log file:
	“1st three answers:” 	-> To see answers at every question.
	“Checking in:”		-> To see at which Rank a particular question is being answered.
	“-----Paragraph  :”	-> To see level and paragraph. 1st number is level, followed by paragraph number.


HOW TO READ RESULTS FILE (after execution):
——————————————————————————————————————————

AnswerMap is written in results file.txt in the same folder with three Ranks. Rank 1 being higher. Use these stats to generate percentages.


EXAMPLE:
———————

	Per Paragraph:

		2_1 : 4/5 : {1: {'What': 1, 'Where': 1}, 2: {'Who': 1, 'When': 1}}

			2_1 				-> level_paragraph
			4/5 				-> 4 questions answered correctly out of 5
			1: {'What': 1, 'Where': 1} 	-> ’What’ and ‘where’ questions are answered by the Rank 1 sentence.
			2: {'Who': 1, 'When': 1} 	-> ‘Who’ and ‘When’ questions are answered by the Rank 2 sentence.


	Per Level:

		2_P : 86/125 C1: 49 C2: 71 C3: 86
			
			2_P 	-> All paragraphs in level 2.
			86/125 	-> 86 questions answered out of 125.
			C1: 49	-> 49 questions answered correctly by Rank 1.
			C2: 71	-> 71 questions answered correctly by Rank 1 and Rank 2.
			C3: 86	-> 86 questions answered correctly by Rank 1 and Rank 2 and Rank 3.


		Correct   : {1: {'When': 15, 'What': 10, 'Who': 8, 'Where': 9, 'Why': 7}, 
				2: {'Where': 9, 'What': 1, 'Who': 5, 'When': 3, 'Why': 4}, 
				3: {'Where': 3, 'Who': 4, 'When': 7, 'Why': 1}}
			
			{1: {'When': 15, 'What': 10, 'Who': 8, 'Where': 9, 'Why': 7} -> Rank 1 answered: 
											15 When questions, 10 What questions, 8 Who questions, 9 Where questions, 7 Why questions.
			
			Similarly for Rank 2 and Rank 3.


		Total Read: {'Where': 26, 'What': 23, 'Who': 26, 'When': 27, 'Why': 23}
			
			Total no. of Where questions attempted	: 26
			Total no. of What questions attempted		: 23
			Total no. of Who questions attempted		: 26
			Total no. of When questions attempted		: 27
			Total no. of Why questions attempted		: 23
