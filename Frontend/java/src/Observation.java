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

    public Observation() {

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

    public Timestamp getTimeObserved() {
        return timeObserved;
    }

    public String getStatus() {
        return status;
    }

    public boolean isFall() {
        return fall;
    }

    public void setRoomNo(int roomNo) {
        this.roomNo = roomNo;
    }

    public void setBpm(int bpm) {
        this.bpm = bpm;
    }

    public void setTemperature(float temperature) {
        this.temperature = temperature;
    }

    public void setTimeObserved(Timestamp timeObserved) {
        this.timeObserved = timeObserved;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public void setFall(boolean fall) {
        this.fall = fall;
    }
}