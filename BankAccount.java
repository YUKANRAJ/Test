public abstract class BankAccount {
    private double Balance;

    public double getBalance() {
        return Balance;
    }

    public void setBalance(double Balance) {
        this.Balance = Balance;
    }

    public double getBal()
    {
        return Balance;
    }
    abstract void withdrawl(double money);
}
