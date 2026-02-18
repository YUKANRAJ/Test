public class SavingsAccount extends Bank { 
	
	@Override
	public void withdraw(Double amount) {
        if (amount <= getBalance()) {
            setBalance(getBalance() - amount);
            System.out.println("Amount Wihthdrawl successfully");

        } else {
            System.out.println("Insufficient balance for withdrawal.");
        }
	}
}
