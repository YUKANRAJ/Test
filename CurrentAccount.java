public class CurrentAccount extends Bank { 
	
	private Double overdraftLimit = 300000000.0;
	
	public Double getOverdraftLimit() {
		return overdraftLimit;
	}
	
	public void setOverdraftLimit(Double limit) {
		this.overdraftLimit = limit;
	}
	
	@Override
	public void withdraw(Double amount) {
		if (amount <= getBalance() + getOverdraftLimit()) {
			setBalance(getBalance() - amount);
			System.out.println("Amount Wihthdrawl successfully");
		} else {
			System.out.println("Withdrawal exceeds overdraft limit");
		}
	}
}