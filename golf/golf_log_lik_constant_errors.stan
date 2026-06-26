data {
  int J;
  array[J] int n;
  vector[J] x;
  array[J] int y;
  real r;
  real R;
}
transformed data {
  vector[J] threshold_angle = asin((R-r) ./ x);
}
parameters {
  real<lower=0> sigma_angle;
  real<lower=0> sigma_distance;
  real<lower=0, upper=1> epsilon;
  real<lower=0> distance_tolerance;
  real<lower=0> overshot;
}
generated quantities {
  vector[J] log_lik;
  vector[J] p_angle = 2*Phi(threshold_angle / sigma_angle) - 1;
  vector[J] p_distance = Phi((distance_tolerance - overshot) ./ ((x + overshot)*sigma_distance)) -
               Phi(-overshot ./ ((x + overshot)*sigma_distance));
  vector[J] p = p_angle .* p_distance * (1 - epsilon);
  for (j in 1:J) {
    log_lik[j] = binomial_lpmf(y[j] | n[j], p[j]);
  }
}
