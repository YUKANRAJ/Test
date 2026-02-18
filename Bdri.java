public class Bdri {

    public static void main(String[] args) {

        // Parent reference → Child object (Polymorphism)
        Bank acc1 = new SavingsAccount();
        acc1.setBalance(10000);
        acc1.withdraw(3000.0);
        acc1.displayBalance();

        System.out.println();

        Bank acc2 = new CurrentAccount();
        acc2.setBalance(5000);
        acc2.withdraw(22000.0);
        acc2.displayBalance();
    }
}
