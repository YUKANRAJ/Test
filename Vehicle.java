public abstract class Vehicle {
    private int speed;

    public int getSpeed() {
        return speed;
    }

    public void setSpeed(int speed) {
        this.speed = speed;
    }
    public void displayspeed()
    {
        System.out.println(getSpeed());
    }
    public abstract void move();
    
}
