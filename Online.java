public abstract class Online {
    private int amount;

    public int getAmount() {
        return amount;
    }

    public void setAmount(int amount) {
        if (amount>0)this.amount = amount;
    }
    public void display()
    {
        System.out.println("AMOUNT:"+getAmount()+" only");

    }
    abstract void pay();
    
    
}
