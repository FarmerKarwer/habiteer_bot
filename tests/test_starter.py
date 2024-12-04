import sys
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from starter import main

class TestMainFunction(unittest.TestCase):
    @patch('starter.handler')
    @patch('starter.handler_long')
    def test_short_handler(self, mock_handler_long, mock_handler):
        # Simulate command-line arguments for short handler
        testargs = ["program", "--handler", "short"]
        with patch.object(sys, 'argv', testargs):
            mock_handler.return_value = {'message': 'Short handler called'}
            
            # Capture stdout
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                self.assertIn('Short handler called', output)
            
            # Verify handler was called correctly
            mock_handler.assert_called_with(event="events/using_command.json", context="Sample context")
            mock_handler_long.assert_not_called()

    @patch('starter.handler')
    @patch('starter.handler_long')
    def test_long_handler(self, mock_handler_long, mock_handler):
        # Simulate command-line arguments for long handler
        testargs = ["program", "--handler", "long"]
        with patch.object(sys, 'argv', testargs):
            mock_handler_long.return_value = {'message': 'Long handler called'}
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                # Assuming no output is expected for long handler
                self.assertEqual(output, '')
            
            mock_handler_long.assert_called_with(event="events/using_command.json", context="Sample context")
            mock_handler.assert_not_called()

    @patch('starter.handler')
    @patch('starter.handler_long')
    def test_default_handler(self, mock_handler_long, mock_handler):
        # Simulate command-line arguments with default handler (long)
        testargs = ["program"]
        with patch.object(sys, 'argv', testargs):
            mock_handler_long.return_value = {'message': 'Long handler called'}
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                self.assertEqual(output, '')
            
            mock_handler_long.assert_called_with(event="events/using_command.json", context="Sample context")
            mock_handler.assert_not_called()

    @patch('starter.handler')
    @patch('starter.handler_long')
    def test_handler_exception(self, mock_handler_long, mock_handler):
        # Simulate command-line arguments and raise exception in handler
        testargs = ["program", "--handler", "short"]
        with patch.object(sys, 'argv', testargs):
            mock_handler.side_effect = Exception("Test exception")
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
                 patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                main()
                output_stdout = mock_stdout.getvalue()
                output_stderr = mock_stderr.getvalue()
                
                self.assertIn("Something Went Wrong", output_stdout)
                self.assertIn("Test exception", output_stdout)
                self.assertIn("Traceback (most recent call last):", output_stderr)
            
            mock_handler_long.assert_not_called()

if __name__ == '__main__':
    unittest.main()
