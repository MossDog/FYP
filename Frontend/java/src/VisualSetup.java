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
    int GRAPH_MARGIN_Y;
    int GRAPH_MARGIN_X;


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
    }


    public void setup()
    {

        colorMode(RGB, 255, 255, 255);
        background(0);
        GRAPH_MARGIN_X = (width - (GRAPH_WIDTH * 2))/3;
        GRAPH_MARGIN_Y = (height - GRAPH_HEIGHT)/3;

    }



    public void draw(){

        background(0);
        displayRoomList();
        if (selectedRoomIndex != -1) {
            displayObservations(selectedRoomIndex);
            drawStatusIndicator();
        }

    }


    public void displayRoomList() {
        textSize(TEXT_SIZE);
        textAlign(LEFT, TOP);
        int yPos = 0;
        for (int i = 0; i < rooms.size(); i++) {
            Room room = rooms.get(i);
            fill(255, 255, 255, 100);
            String status = dbDao.getRecentstatusByRoomNo(rooms.get(i).getRoomNo());
            String text = "Room " + room.getRoomNo();


            if (i == selectedRoomIndex) {
                fill(255);
                stroke(getColor(status));
                rect(20, yPos, (int)((TEXT_SIZE * text.length()) * 0.6), TEXT_SIZE+5);
                fill(0);
                text(text, 20, yPos);
            } else {
                fill(0);
                stroke(getColor(status));
                rect(20, yPos, (int)((TEXT_SIZE * text.length()) * 0.6), TEXT_SIZE+5);
                fill(255);
                text(text, 20, yPos);
            }

            
            
            yPos += TEXT_SIZE+10;
        }
    }


    public void displayObservations(int roomIndex) {
        observations = dbDao.getRecentObservationsByRoomNo(rooms.get(roomIndex).getRoomNo());
        for (Observation obs : observations){
            System.out.println(obs.toString());
        }
        System.out.println("OBSERVATIONS LENGTH: " + observations.size());
        
        // Draw BPM graph
        drawGraph(observations, "BPM", GRAPH_MARGIN_X, GRAPH_MARGIN_Y, GRAPH_WIDTH, GRAPH_HEIGHT);
        
        // Draw temperature graph
        drawGraph(observations, "Temperature", (GRAPH_MARGIN_X * 2) + GRAPH_WIDTH, GRAPH_MARGIN_Y, GRAPH_WIDTH, GRAPH_HEIGHT);
    }


    public void drawGraph(List<Observation> observations, String parameter, int xPos, int yPos, int width, int height) {
        // Find max and min values
        float maxValue = Float.MIN_VALUE;
        float minValue = Float.MAX_VALUE;
        for (Observation obs : observations) {
            float value = (parameter.equals("BPM")) ? obs.getBpm() : obs.getTemperature();
            if (value > maxValue) {
                maxValue = value;
            }
            if (value < minValue) {
                minValue = value;
            }
        }
        
        // Draw graph axes
        fill(255);
        stroke(255);
        strokeWeight(2);
        line(xPos, yPos + height, xPos + width, yPos + height); // X-axis
        line(xPos, yPos, xPos, yPos + height); // Y-axis
        
        // Draw graph data points
        float yIncrement = (float) height / (maxValue - minValue);
        float xIncrement = (float) width / (observations.size() - 1); // Calculate x-increment based on the number of observations
        float x = xPos;
        float previousX = xPos;
        float previousY = yPos + height - (observations.get(observations.size() - 1).getBpm() - minValue) * yIncrement; // Use the last observation's value
        if (parameter.equals("Temperature")) {
            previousY = yPos + height - (observations.get(observations.size() - 1).getTemperature() - minValue) * yIncrement;
        }
        for (int i = observations.size() - 1; i >= 0; i--) {
            float value = (parameter.equals("BPM")) ? observations.get(i).getBpm() : observations.get(i).getTemperature();
            float y = yPos + height - (value - minValue) * yIncrement;
            stroke(255, 0, 0);
            strokeWeight(5);
            line(previousX, previousY, x, y);
            previousX = x;
            previousY = y;
            x += xIncrement; // Increment x position
        }
        
        // Label axes
        textSize(TEXT_SIZE / 2);
        textAlign(CENTER, CENTER);
        fill(255);
        text("Time", xPos + width / 2, yPos + height + GRAPH_MARGIN_Y / 2);
        if (parameter.equals("BPM")) {
            text("BPM", xPos - GRAPH_MARGIN_Y / 2, yPos + height / 2);
        } else {
            text("Temperature", xPos - GRAPH_MARGIN_Y / 2, yPos + height / 2);
        }
    
        // Draw tick marks and labels on the x-axis
        stroke(255);
        int numXTicks = observations.size()-1; // Limit the number of x-axis ticks to 10
        x = xPos; // Reset x position
        for (int i = 0; i <= numXTicks; i++) {
            line(x, yPos + height - 5, x, yPos + height + 5); // Draw tick mark
            String timestamp = observations.get(i).getTimeObserved().toString(); // Assuming time_observed is a Timestamp object
            String label = timestamp.substring(11, 16); // Extract hour and minute
            textAlign(CENTER, TOP);
            text(label, x, yPos + height + 10); // Draw label
            x += xIncrement; // Increment x position
        }
    
        // Draw tick marks and labels on the y-axis
        int numYTicks = 5; // Number of tick marks on the y-axis
        yIncrement = height / (float) numYTicks;
        float tickValueIncrement = (maxValue - minValue) / (float) numYTicks;
        for (int i = 0; i <= numYTicks; i++) {
            float y = yPos + height - i * yIncrement;
            line(xPos - 5, y, xPos + 5, y); // Draw tick mark
            float labelValue = minValue + i * tickValueIncrement;
            String label = nf(labelValue, 0, 1); // Format the label (optional)
            textAlign(RIGHT, CENTER);
            text(label, xPos - 10, y); // Draw label
        }
    }
    


    public void drawStatusIndicator() {
        String lastStatus = observations.get(0).getStatus();
        int colorBoxWidth = 100;
        int colorBoxHeight = 50;
        int colorBoxX = GRAPH_MARGIN_X + GRAPH_WIDTH + (GRAPH_MARGIN_X/2) - (colorBoxWidth/2); // Adjust the x position as needed
        int colorBoxY = (GRAPH_MARGIN_Y * 2) + GRAPH_HEIGHT; // Adjust the y position as needed
        fill(getColor(lastStatus));
        rect(colorBoxX, colorBoxY, colorBoxWidth, colorBoxHeight);
        fill(0);
        textAlign(CENTER, CENTER);
        text("Status: " + lastStatus.toUpperCase(), colorBoxX + colorBoxWidth / 2, colorBoxY + colorBoxHeight / 2);
    }
    

    // Helper function to map status string to color
    private int getColor(String status) {
        switch (status.toLowerCase()) {
            case "green":
                return color(0, 255, 0);
            case "orange":
                return color(255, 165, 0);
            case "red":
                return color(255, 0, 0);
            default:
                return color(255); // Default color (white)
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