import unittest
import numpy as np
from Server import process_frame
from Server import decide_status
from Server import store_observation
from unittest.mock import patch

# Import DbDao directly
from DbDao import add_room
from DbDao import add_Obervation
from DbDao import get_room_by_number

class ServerTests(unittest.TestCase):
    def test_process_frame(self):
        # Mock frame data
        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        # Call the function
        result = process_frame(frame)

        # Assert that the result is within expected range or None
        self.assertTrue(result is None or (result >= -90 and result <= 90))


    def test_decide_status_green(self):
        # Test with normal parameters
        result = decide_status(80, 21, False)
        self.assertEqual(result, "green")

    def test_decide_status_orange(self):
        # Test with elevated heart rate
        result = decide_status(140, 21, False)
        self.assertEqual(result, "orange")

    def test_decide_status_red(self):
        # Test with extreme conditions
        result = decide_status(40, 17, True)
        self.assertEqual(result, "red")


    @patch('DbDao.add_room', return_value=None)
    @patch('DbDao.add_observation', return_value=None)
    def test_store_observation(self, mock_add_observation, mock_add_room):
        # Call the function with different combinations of parameters
        store_observation("Room1", 30, 70, 22, False, "green")

        # Assert that the database methods were called with the correct arguments
        mock_add_room.assert_called_once_with("Room1", 30)
        mock_add_observation.assert_called_once_with("Room1", 70, 22, False, "green")

        # Call the function with different room numbers and user ages
        store_observation("Room2", 25, 80, 23, True, "red")
        store_observation("Room3", 40, 60, 20, False, "orange")

        # Assert that the database methods were called with the correct arguments
        mock_add_room.assert_any_call("Room2", 25)
        mock_add_observation.assert_any_call("Room2", 80, 23, True, "red")
        mock_add_room.assert_any_call("Room3", 40)
        mock_add_observation.assert_any_call("Room3", 60, 20, False, "orange")

    def test_store_observation_room_not_exists(self):
        # Test when the room does not exist in the database
        with patch('DbDao.get_room_by_no', return_value=None) as mock_get_room_by_no:
            with patch('DbDao.add_room', return_value=None) as mock_add_room:
                with patch('DbDao.add_observation', return_value=None) as mock_add_observation:
                    store_observation("Room4", 35, 75, 21, True, "red")

                    # Assert that the room was added to the database
                    mock_get_room_by_no.assert_called_once_with("Room4")
                    mock_add_room.assert_called_once_with("Room4", 35)
                    mock_add_observation.assert_called_once_with("Room4", 75, 21, True, "red")

    def test_store_observation_room_exists(self):
        # Test when the room already exists in the database
        with patch('DbDao.get_room_by_no', return_value=True) as mock_get_room_by_no:
            with patch('DbDao.add_room') as mock_add_room:
                with patch('DbDao.add_observation', return_value=None) as mock_add_observation:
                    store_observation("Room5", 45, 65, 24, False, "green")

                    # Assert that the room was not added again to the database
                    mock_get_room_by_no.assert_called_once_with("Room5")
                    mock_add_room.assert_not_called()
                    mock_add_observation.assert_called_once_with("Room5", 65, 24, False, "green")

if __name__ == '__main__':
    unittest.main()
