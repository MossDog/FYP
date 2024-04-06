import processing.core.PApplet;
import java.util.TimerTask;
import java.util.Timer;
import java.util.List;


public class VisualSetup extends PApplet
{

    DbDao dbDao;
    List<Room> rooms;
    List<Observation> observations;
    int selectedRoomIndex = 0;
    int TEXT_SIZE = 30;
    int GRAPH_WIDTH = 500;
    int GRAPH_HEIGHT = 500;
    int GRAPH_MARGIN = 150;

    //settings
    public void settings()
    {
        size(1920, 1080);
        println("CWD: " + System.getProperty("user.dir"));
        dbDao = new DbDao();
        fullScreen();
        System.out.println("entering refresh data");
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
        textSize(TEXT_SIZE);
        textAlign(LEFT, TOP);
        int yPos = 0;
        for (int i = 0; i < rooms.size(); i++) {
            Room room = rooms.get(i);
            fill(255, 255, 255, 100);
            String text = "Room " + room.getRoomNo();
            rect(20, yPos, (int)((TEXT_SIZE * text.length()) * 0.6), TEXT_SIZE+5);
            if (i == selectedRoomIndex) {
                fill(255, 0, 0);
            } else {
                fill(0);
            }
            text(text, 20, yPos);
            yPos += TEXT_SIZE+10;
        }
    }


    public void displayObservations(int roomIndex) {
        //observations = dbDao.getObservationsByRoomAndTimeRange(rooms.get(roomIndex).getRoomNo(), System.currentTimeMillis() - 60000, System.currentTimeMillis());
        observations = dbDao.getObservationsByRoomNo(rooms.get(roomIndex).getRoomNo());
        System.out.println("OBSERVATIONS LENGTH: " + observations.size());
        
        // Draw BPM graph
        drawGraph(observations, "BPM", 300, GRAPH_MARGIN, GRAPH_WIDTH, GRAPH_HEIGHT);
        
        // Draw temperature graph
        drawGraph(observations, "Temperature", 300 + GRAPH_WIDTH + 100, GRAPH_MARGIN, GRAPH_WIDTH, GRAPH_HEIGHT);
    }


    public void drawGraph(List<Observation> observations, String parameter, int xPos, int yPos, int width, int height) {
        System.out.println("IN DRAW GRAPH");
        // Find max value
        float maxValue = Float.MIN_VALUE;
        for (Observation obs : observations) {
            float value = (parameter.equals("BPM")) ? obs.getBpm() : obs.getTemperature();
            if (value > maxValue) {
                maxValue = value;
            }
        }
        
        // Draw graph axes
        fill(255);
        stroke(255);
        strokeWeight(2);
        line(xPos, yPos + height, xPos + width, yPos + height); // X-axis
        line(xPos, yPos, xPos, yPos + height); // Y-axis
        
        // Draw graph data points
        float xIncrement = (float) width / (observations.size() - 1);
        float yIncrement = (float) height / maxValue;
        float x = xPos;
        float previousX = xPos;
        float previousY = yPos + height - observations.get(0).getBpm() * yIncrement;
        System.out.println("ENTERING LOOP");
        for (int i = 0; i < observations.size(); i++) {
            System.out.println("IN LOOP");
            float value = (parameter.equals("BPM")) ? observations.get(i).getBpm() : observations.get(i).getTemperature();
            float y = yPos + height - value * yIncrement;
            stroke(255,0,0);
            strokeWeight(5);
            line(previousX, previousY, x, y);
            System.out.println("GRAPH LINE POINTS: " + previousX + " " + previousY + " " + x + " " + y);
            previousX = x;
            previousY = y;
            x += xIncrement;
        }
        
        // Label axes
        textSize(TEXT_SIZE / 2);
        textAlign(CENTER, CENTER);
        fill(255);
        text("Time", xPos + width / 2, yPos + height + GRAPH_MARGIN / 2);
        if (parameter.equals("BPM")) {
            text("BPM", xPos - GRAPH_MARGIN / 2, yPos + height / 2);
        } else {
            text("Temperature", xPos - GRAPH_MARGIN / 2, yPos + height / 2);
        }
    }


    public void mouseClicked() {
        int clickedIndex = mouseY / (TEXT_SIZE+10);
        if (clickedIndex >= 0 && clickedIndex < rooms.size()) {
            selectedRoomIndex = clickedIndex;
        }
        refreshData();
    }


    private void refreshData() {
        rooms = dbDao.getAllRooms();
        if (selectedRoomIndex >= 0 && selectedRoomIndex < rooms.size()) {
            observations = dbDao.getObservationsByRoomNo(rooms.get(selectedRoomIndex).getRoomNo());
        }
    }


}//end