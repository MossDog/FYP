
public class Main
{	

	public void startUI()
	{
		String[] a = {"MAIN"};
        processing.core.PApplet.runSketch( a, new VisualSetup());		
	}

	public static void main(String[] args)
	{
		System.out.println("Hello World");
		Main main = new Main();
		main.startUI();	
	}
}