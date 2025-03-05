import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from main import read_tickets, evaluate_reply, process_evaluation

class TestSolution(unittest.TestCase):
    def test_read_tickets(self):
        # Test reading a valid CSV file
        df = read_tickets('test_tickets.csv')
        self.assertIsInstance(df, pd.DataFrame)
        
        # Test handling of file not found
        with self.assertRaises(FileNotFoundError):
            read_tickets('non_existent.csv')
        
        # Test handling of empty file
        with patch('pandas.read_csv', side_effect=pd.errors.EmptyDataError):
            with self.assertRaises(pd.errors.EmptyDataError):
                read_tickets('empty.csv')

    @patch('solution.client.chat.completions.create')
    def test_evaluate_reply(self, mock_create):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.__getitem__.return_value = [{'message': {'content': 'Content Score: 5, Content Explanation: Good, Format Score: 5, Format Explanation: Well structured'}}]
        mock_create.return_value = mock_response
        
        # Test evaluation
        result = evaluate_reply('Test ticket', 'Test reply')
        self.assertIn('Content Score', result)

    def test_process_evaluation(self):
        evaluation = 'Content Score: 5, Content Explanation: Good, Format Score: 5, Format Explanation: Well structured'
        content_score, content_explanation, format_score, format_explanation = process_evaluation(evaluation)
        
        self.assertEqual(content_score, 5)
        self.assertEqual(content_explanation, 'Good')
        self.assertEqual(format_score, 5)
        self.assertEqual(format_explanation, 'Well structured')

if __name__ == '__main__':
    unittest.main()
