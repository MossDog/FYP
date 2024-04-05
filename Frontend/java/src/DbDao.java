import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

public class DbDao {

    private static final String DB_URL = "jdbc:mysql://localhost:3306/DB";
    private static final String USERNAME = "mossdog";
    private static final String PASSWORD = "mossdog";

    private Connection conn = null;

    public DbDao() {
        try {
            conn = DriverManager.getConnection(DB_URL, USERNAME, PASSWORD);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void disconnect() {
        if (conn != null) {
            try {
                conn.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }

    public List<Room> getAllRooms() {
        List<Room> rooms = new ArrayList<>();
        String query = "SELECT * FROM Room";
        try (PreparedStatement statement = conn.prepareStatement(query)) {
            ResultSet resultSet = statement.executeQuery();
            while (resultSet.next()) {
                int roomNo = resultSet.getInt("room_no");
                int age = resultSet.getInt("age");
                Room room = new Room(roomNo, age);
                rooms.add(room);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return rooms;
    }

    public List<Observation> getObservationsByRoomNo(int roomNo) {
        List<Observation> observations = new ArrayList<>();
        String query = "SELECT * FROM Observation WHERE room_no = ?";
        try (PreparedStatement statement = conn.prepareStatement(query)) {
            statement.setInt(1, roomNo);
            ResultSet resultSet = statement.executeQuery();
            while (resultSet.next()) {
                int bpm = resultSet.getInt("bpm");
                float temperature = resultSet.getFloat("temperature");
                boolean fall = resultSet.getBoolean("fall");
                Timestamp timeObserved = resultSet.getTimestamp("time_observed");
                String status = resultSet.getString("status");
                Observation observation = new Observation(roomNo, bpm, temperature, fall, timeObserved, status);
                observations.add(observation);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return observations;
    }
}
