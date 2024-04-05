import java.sql.Timestamp;

public class Observation {
    private int roomNo;
    private int bpm;
    private float temperature;
    private boolean fall;
    private Timestamp timeObserved;
    private String status;

    public Observation(int roomNo, int bpm, float temperature, boolean fall, Timestamp timeObserved, String status) {
        this.roomNo = roomNo;
        this.bpm = bpm;
        this.temperature = temperature;
        this.fall = fall;
        this.timeObserved = timeObserved;
        this.status = status;
    }

    public int getRoomNo() {
        return roomNo;
    }

    public int getBpm() {
        return bpm;
    }

    public float getTemperature() {
        return temperature;
    }

    public boolean isFall() {
        return fall;
    }

    public Timestamp getTimeObserved() {
        return timeObserved;
    }

    public String getStatus() {
        return status;
    }
}
