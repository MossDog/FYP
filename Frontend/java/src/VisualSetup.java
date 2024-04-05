import processing.core.PApplet;
import java.util.TimerTask;
import java.util.Timer;
import java.util.List;


public class VisualSetup extends PApplet
{

    DbDao dbDao;
    List<Room> rooms;
    List<Observation> observations;
    int selectedRoomIndex = -1;

    //settings
    public void settings()
    {
        size(1920, 1080);
        println("CWD: " + System.getProperty("user.dir"));
        dbDao = new DbDao();
        fullScreen();
        refreshData(); // Initial data load
        // Schedule periodic data refresh
        Timer timer = new Timer();
        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                refreshData();
            }
        }, 5000L, 5000L); // Refresh data every 5 seconds
    }//end settings


    //setup
    public void setup()
    {

        colorMode(RGB, 255, 255, 255);
        background(0);

    }//end setup


    //draw
    public void draw(){

        background(0);
        displayRoomList();
        if (selectedRoomIndex != -1) {
            displayObservations(selectedRoomIndex);
        }

    }//end draw


    public void displayRoomList() {
        fill(255);
        textSize(20);
        textAlign(LEFT, TOP);
        int yPos = 20;
        for (int i = 0; i < rooms.size(); i++) {
            Room room = rooms.get(i);
            if (i == selectedRoomIndex) {
                fill(255, 0, 0);
            } else {
                fill(255);
            }
            text("Room " + room.getRoomNo(), 20, yPos);
            yPos += 30;
        }
    }


    public void displayObservations(int roomIndex) {
        int xPos = width / 2 + 50;
        int yPos = 50;
        observations = dbDao.getObservationsByRoomNo(rooms.get(roomIndex).getRoomNo());
        for (Observation obs : observations) {
            fill(255);
            text("BPM: " + obs.getBpm(), xPos, yPos);
            text("Temperature: " + obs.getTemperature(), xPos, yPos + 20);
            yPos += 50;
        }
    }


    public void mouseClicked() {
        int clickedIndex = mouseY / 30;
        if (clickedIndex >= 0 && clickedIndex < rooms.size()) {
            selectedRoomIndex = clickedIndex;
        }
    }


    private void refreshData() {
        rooms = dbDao.getAllRooms();
        if (selectedRoomIndex >= 0 && selectedRoomIndex < rooms.size()) {
            observations = dbDao.getObservationsByRoomNo(rooms.get(selectedRoomIndex).getRoomNo());
        }
    }


}//end