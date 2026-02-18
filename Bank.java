public abstract class Bank{
    private static double balance=0;

    public double getBalance() {
        return balance;
    }

    public void setBalance(double balance) {
        
        this.balance = balance;
    }

    public void displayBalance() {
        System.out.println("Current Balance: $" + balance);
    }

    public abstract void withdraw(Double amount);
}