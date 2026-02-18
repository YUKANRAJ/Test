import java.util.Scanner;

public class DriDri {
    public static void main(String[] args) {
        Scanner s=new Scanner(System.in);
        Vehicle c=new Bike();
        Vehicle b=new Car();
        System.out.print("BIKE ENNA SPEED LA POGUM:");
        c.setSpeed(s.nextInt());
        c.move();
        System.out.print("CAR ENNA SPEED LA POGUM");
        b.setSpeed(s.nextInt());
        b.move();


    }

}
